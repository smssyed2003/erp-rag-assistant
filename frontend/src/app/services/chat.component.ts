import { Component, ViewChild, ElementRef } from '@angular/core';
import { ChatService } from './chat.service';

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

  @ViewChild('chatBox') chatBox!: ElementRef;

  userInput: string = '';
  messages: ChatMessage[] = [];
  sessionId = Math.random().toString(36).substring(7);
  isLoading = false;
  errorMessage = '';

  constructor(private chatService: ChatService) {}

  sendMessage() {
    const question = this.userInput.trim();
    if (!question || this.isLoading) return;

    // ✅ Add user message
    this.messages.push({
      role: 'user',
      text: question
    });

    this.userInput = '';
    this.errorMessage = '';
    this.isLoading = true;

    this.scrollToBottom(); // ✅ scroll after user message

    // ✅ Call backend
    this.chatService.askQuestion(question, this.sessionId).subscribe({
      next: (res: any) => {

        this.messages.push({
          role: 'bot',
          text: typeof res.response === 'string'
            ? res.response
            : res.response?.answer || res.answer || 'No response',
          sources: res.response?.sources || res.sources || []
        });

        this.scrollToBottom(); // ✅ scroll after bot message
      },

      error: (err) => {
        console.error(err);
        this.errorMessage = 'Unable to get an answer from the backend. Please try again.';
        this.isLoading = false;
      },

      complete: () => {
        this.isLoading = false;
      }
    });
  }

  // ✅ Reusable scroll function
  scrollToBottom() {
    setTimeout(() => {
      if (this.chatBox) {
        this.chatBox.nativeElement.scrollTop =
          this.chatBox.nativeElement.scrollHeight;
      }
    }, 100);
  }
}