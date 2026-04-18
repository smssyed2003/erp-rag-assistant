import { Component } from '@angular/core';
import { ChatService, ChatResponse } from './chat.service';

interface ChatMessage {
  role: 'user' | 'bot';
  text: string;
  sources?: string[];
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent {
  userInput: string = '';
  messages: ChatMessage[] = [];
  sessionId = Math.random().toString(36).substring(7);
  isLoading = false;
  errorMessage = '';

  constructor(private chatService: ChatService) {}

  sendMessage() {
    if (!this.userInput.trim()) {
      return;
    }

    const question = this.userInput.trim();
    this.messages.push({ role: 'user', text: question });
    this.userInput = '';
    this.errorMessage = '';
    this.isLoading = true;

    this.chatService.askQuestion(question, this.sessionId).subscribe({
      next: (res: ChatResponse) => {
        this.messages.push({
          role: 'bot',
          text: res.answer,
          sources: res.sources
        });
      },
      error: (error) => {
        console.error(error);
        this.errorMessage = 'Unable to get an answer from the backend. Please try again.';
      },
      complete: () => {
        this.isLoading = false;
      }
    });
  }
}
