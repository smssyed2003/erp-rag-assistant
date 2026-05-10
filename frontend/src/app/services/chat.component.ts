import { Component, ElementRef, ViewChild, AfterViewChecked, inject } from '@angular/core';
import { ChatService, ChatResponse } from './chat.service';

interface ChatMessage {
  role: 'user' | 'bot';
  text: string;
  sources?: string[];
  id: string;
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent implements AfterViewChecked {
  userInput = '';
  messages: ChatMessage[] = [];
  sessionId = Math.random().toString(36).substring(7);
  isLoading = false;
  errorMessage = '';

  @ViewChild('chatMessages') private chatMessagesContainer!: ElementRef;
  @ViewChild('messageInput') private messageInput!: ElementRef;

  private chatService = inject(ChatService);

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  trackByMessage(index: number, message: ChatMessage): string {
    return message.id;
  }

  sendMessage() {
    if (!this.userInput.trim() || this.isLoading) {
      return;
    }

    const question = this.userInput.trim();
    const messageId = Date.now().toString();

    this.messages.push({
      role: 'user',
      text: question,
      id: messageId
    });

    this.userInput = '';
    this.errorMessage = '';
    this.isLoading = true;

    // Focus back to input after sending
    setTimeout(() => {
      if (this.messageInput) {
        this.messageInput.nativeElement.focus();
      }
    }, 0);

    this.chatService.askQuestion(question, this.sessionId).subscribe({
      next: (res: ChatResponse) => {
        this.messages.push({
          role: 'bot',
          text: res.answer,
          sources: res.sources,
          id: (Date.now() + 1).toString()
        });
      },
      error: (error) => {
        console.error('Chat error:', error);
        this.errorMessage = 'Unable to get an answer from the backend. Please check your connection and try again.';
        this.isLoading = false;
      },
      complete: () => {
        this.isLoading = false;
      }
    });
  }

  clearError() {
    this.errorMessage = '';
  }

  private scrollToBottom(): void {
    try {
      if (this.chatMessagesContainer) {
        this.chatMessagesContainer.nativeElement.scrollTop =
          this.chatMessagesContainer.nativeElement.scrollHeight;
      }
    } catch (err) {
      console.error('Scroll error:', err);
    }
  }
}
