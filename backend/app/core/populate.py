import asyncio
import logging
import os
import sys
from typing import Any, Dict, Set
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from core.config import settings
from models.card import Card  # Adjust import path as needed
from services.scryfall import ScryfallService  # Import your existing service
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker


# Import your existing models and database configuration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MTGDatabasePopulator:
    def __init__(self, database_url: str):
        # Convert the database URL to use asyncpg if needed
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace(
                'postgresql://', 'postgresql+asyncpg://', 1)

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

    async def get_session(self) -> AsyncSession: # type: ignore
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
        """
        Transform Scryfall card data to match our database schema with safe handling of missing attributes.
        Returns a dictionary with all required fields, using appropriate default values when data is missing.
        """
        # Initialize image URIs and card faces
        image_uri = None
        back_image_uri = None
        card_faces = None
        
        # Safe handling of card faces and images
        if 'card_faces' in card_data and card_data['card_faces']:
            card_faces = card_data['card_faces']
            front_face = card_faces[0]
            
            # Handle front face image
            if 'image_uris' in front_face:
                image_uri = front_face['image_uris'].get('normal', '')
            
            # Handle back face image if it exists
            if len(card_faces) > 1 and 'image_uris' in card_faces[1]:
                back_image_uri = card_faces[1]['image_uris'].get('normal', '')
        else:
            # Handle single-faced card image
            image_uri = card_data.get('image_uris', {}).get('normal', '')

        # Get data from appropriate source (front face or main card)
        if card_faces:
            front_face = card_faces[0]
            mana_cost = front_face.get('mana_cost', '')
            oracle_text = front_face.get('oracle_text', '')
            type_line = front_face.get('type_line', '')
            power = front_face.get('power', '')
            toughness = front_face.get('toughness', '')
        else:
            mana_cost = card_data.get('mana_cost', '')
            oracle_text = card_data.get('oracle_text', '')
            type_line = card_data.get('type_line', '')
            power = card_data.get('power', '')
            toughness = card_data.get('toughness', '')

        # Extract price safely
        prices = card_data.get('prices', {})
        usd_price = prices.get('usd')
        try:
            price = float(usd_price) if usd_price is not None else 0.0
        except (ValueError, TypeError):
            price = 0.0

        # Extract CMC safely
        try:
            cmc = float(card_data.get('cmc', 0))
        except (ValueError, TypeError):
            cmc = 0.0

        # Build the transformed data dictionary with safe defaults
        transformed_data = {
            'id': card_data.get('id', ''),  # This should never be empty in practice
            'name': card_data.get('name', 'Unknown'),  # Provide a default name
            'mana_cost': mana_cost or '',
            'cmc': cmc,
            'color_identity': card_data.get('color_identity', []),
            'type_line': type_line or '',
            'oracle_text': oracle_text or '',
            'power': power or '',
            'toughness': toughness or '',
            'rarity': card_data.get('rarity', ''),
            'set_code': card_data.get('set', ''),
            'collector_number': card_data.get('collector_number', ''),
            'image_uri': image_uri or '',
            'back_image_uri': back_image_uri or '',
            'keywords': card_data.get('keywords', []),
            'legalities': card_data.get('legalities', {}),
            'price': price,
            'vector_embedding': None,  # Keep as None for now
            'layout': card_data.get('layout', 'normal'),
            'card_faces': card_faces if card_faces else None
        }

        # Validate required fields
        if not transformed_data['id'] or not transformed_data['name']:
            raise ValueError(f"Card data missing required fields: {card_data}")

        # Ensure arrays are actually arrays
        transformed_data['color_identity'] = (
            transformed_data['color_identity'] 
            if isinstance(transformed_data['color_identity'], list) 
            else []
        )
        transformed_data['keywords'] = (
            transformed_data['keywords'] 
            if isinstance(transformed_data['keywords'], list) 
            else []
        )

        # Ensure JSON fields are dictionaries
        transformed_data['legalities'] = (
            transformed_data['legalities'] 
            if isinstance(transformed_data['legalities'], dict) 
            else {}
        )

        # Validate numeric fields
        if not isinstance(transformed_data['cmc'], (int, float)):
            transformed_data['cmc'] = 0.0
        if not isinstance(transformed_data['price'], (int, float)):
            transformed_data['price'] = 0.0

        return transformed_data

    async def update_card(self, session: AsyncSession, card_data: Dict[str, Any]) -> bool:
        """Update or insert a card in the database. Returns True if successful."""
        try:
            transformed_data = self.transform_card_data(card_data)
        except ValueError as e:
            logger.error(f"Invalid card data: {e}")
            return False
        except Exception as e:
            logger.error(f"Error transforming card data: {e}")
            return False

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
            
            return True

        except Exception as e:
            logger.error(
                f"Error processing card {transformed_data.get('name', 'Unknown')}: {str(e)}")
            return False

    async def populate_database(self):
        """Populate the database with Standard-legal cards"""
        logger.info("Starting database population...")
        async with ScryfallService() as scryfall:
            try:
                cards_processed = 0
                cards_failed = 0
                batch_size = 0
                current_session = None

                async for card_data in scryfall.get_standard_legal_cards():
                    logger.debug(f"Retrieved card from Scryfall: {card_data['name']} (ID: {card_data['id']})")
                    # Create new session every 100 cards
                    if batch_size == 0:
                        if current_session:
                            await current_session.commit()
                            await current_session.close()
                        current_session = self.async_session()

                    try:
                        # Process the card as a single entity, regardless of faces
                        success = await self.update_card(current_session, card_data)

                        if success:
                            cards_processed += 1
                            batch_size += 1

                        # Commit every 100 cards
                        if batch_size >= 100:
                            await current_session.commit()
                            logger.info(f"Successfully processed {cards_processed} cards (Failed: {cards_failed})")
                            batch_size = 0

                    except Exception as e:
                        cards_failed += 1
                        logger.error(f"Error processing card batch: {str(e)}")
                        await current_session.rollback()
                        continue

                # Final commit for any remaining cards
                if current_session and batch_size > 0:
                    await current_session.commit()
                    await current_session.close()

                logger.info(
                    f"Database population completed. Total cards processed: {cards_processed}, Failed: {cards_failed}")

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
