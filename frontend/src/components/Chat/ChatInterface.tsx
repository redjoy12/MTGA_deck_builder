import React, { useState } from 'react';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { ChatMessage } from '../../types';
import { useDeck } from '../../context/DeckContext';

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { currentDeck } = useDeck();

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content,
      sender: 'user',
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Here you would typically make an API call to your backend
      // For now, we'll simulate a response
      setTimeout(() => {
        const aiMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          content: `I'm analyzing your deck with ${currentDeck?.cards.length || 0} cards. What specific advice would you like?`,
          sender: 'ai',
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, aiMessage]);
        setIsLoading(false);
      }, 1000);
      
    } catch (error) {
      console.error('Failed to get AI response:', error);
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[600px] border rounded-lg bg-white shadow-lg">
      <div className="bg-gray-50 border-b p-4">
        <h2 className="text-lg font-semibold">Deck Building Assistant</h2>
      </div>
      
      <MessageList messages={messages} />
      
      <MessageInput 
        onSendMessage={handleSendMessage}
        disabled={isLoading}
      />
    </div>
  );
};