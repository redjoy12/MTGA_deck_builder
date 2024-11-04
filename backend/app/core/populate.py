from typing import Set, Dict, Any
import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select

# Import your existing models and database configuration
from models.card import Card  # Adjust import path as needed
from services.scryfall import ScryfallService  # Import your existing service
from core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MTGDatabasePopulator:
    def __init__(self, database_url: str):
        # Convert the database URL to use asyncpg if needed
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
        
        self.engine = create_async_engine(
            database_url,
            echo=True,
            pool_pre_ping=True
        )
        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        self.standard_sets: Set[str] = set()

    async def get_session(self) -> AsyncSession:
        session = self.async_session()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

    def transform_card_data(self, card_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Scryfall card data to match our existing database schema"""
        # Extract image URI, handling double-faced cards
        image_uri = (
            card_data.get('image_uris', {}).get('normal')
            if 'image_uris' in card_data
            else card_data.get('card_faces', [{}])[0].get('image_uris', {}).get('normal')
        )
        
        # Only include fields that exist in our database schema
        return {
            'id': card_data['id'],
            'name': card_data['name'],
            'mana_cost': card_data.get('mana_cost', ''),
            'cmc': float(card_data.get('cmc', 0)),
            'colors': card_data.get('colors', []),
            'type_line': card_data.get('type_line', ''),
            'oracle_text': card_data.get('oracle_text', ''),
            'power': card_data.get('power', ''),
            'toughness': card_data.get('toughness', ''),
            'rarity': card_data.get('rarity', ''),
            'set_code': card_data.get('set', ''),
            'image_uri': image_uri,
            'vector_embedding': None  # Maintain this field as is
        }

    async def update_card(self, session: AsyncSession, card_data: Dict[str, Any]):
        """Update or insert a card in the database"""
        transformed_data = self.transform_card_data(card_data)
        
        try:
            stmt = select(Card).where(Card.id == transformed_data['id'])
            result = await session.execute(stmt)
            existing_card = result.scalar_one_or_none()
            
            if existing_card:
                for key, value in transformed_data.items():
                    setattr(existing_card, key, value)
                logger.info(f"Updated card: {existing_card.name}")
            else:
                new_card = Card(**transformed_data)
                session.add(new_card)
                logger.info(f"Added new card: {transformed_data['name']}")
                
        except Exception as e:
            logger.error(f"Error processing card {transformed_data.get('name', 'Unknown')}: {str(e)}")
            raise

    async def populate_database(self):
        """Populate the database with Standard-legal cards"""
        async with ScryfallService() as scryfall:
            try:
                cards_processed = 0
                batch_size = 0
                current_session = None
                
                async for card_data in scryfall.get_standard_legal_cards():
                    # Create new session every 100 cards
                    if batch_size == 0:
                        if current_session:
                            await current_session.commit()
                            await current_session.close()
                        current_session = self.async_session()
                        
                    try:
                        if 'card_faces' in card_data:
                            # Handle double-faced cards
                            for face in card_data['card_faces']:
                                merged_data = {**card_data, **face}
                                await self.update_card(current_session, merged_data)
                        else:
                            await self.update_card(current_session, card_data)
                            
                        cards_processed += 1
                        batch_size += 1
                        
                        # Commit every 100 cards
                        if batch_size >= 100:
                            await current_session.commit()
                            logger.info(f"Processed {cards_processed} cards")
                            batch_size = 0
                            
                    except Exception as e:
                        logger.error(f"Error processing card batch: {str(e)}")
                        await current_session.rollback()
                        continue
                
                # Final commit for any remaining cards
                if current_session and batch_size > 0:
                    await current_session.commit()
                    await current_session.close()
                
                logger.info(f"Database population completed. Total cards processed: {cards_processed}")
                
            except Exception as e:
                logger.error(f"Error populating database: {str(e)}")
                raise

async def main():
    # Replace with your actual database URL
    database_url = settings.get_database_url
    
    populator = MTGDatabasePopulator(database_url)
    await populator.populate_database()

if __name__ == "__main__":
    asyncio.run(main())