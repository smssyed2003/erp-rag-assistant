import { Component, ViewChild, ElementRef } from '@angular/core';
import { ChatService, AgentStep } from './chat.service';

interface ChatMessage {
  role: 'user' | 'bot';
  text: string;
  sources?: string[];
  steps?: AgentStep[];
  isTyping?: boolean;
  expandSteps?: boolean;
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

    this.messages.push({
      role: 'user',
      text: question
    });

    const botIndex = this.messages.length;
    this.messages.push({
      role: 'bot',
      text: '',
      sources: [],
      steps: [],
      isTyping: true,
      expandSteps: false
    });

    this.userInput = '';
    this.errorMessage = '';
    this.isLoading = true;
    this.scrollToBottom();

    this.chatService.askQuestion(question, this.sessionId).subscribe({
      next: (res: any) => {
        const answer = res.answer || res.response?.answer || res.response || 'No response';
        const sources = res.sources || res.response?.sources || [];
        const steps = res.steps || [];

        this.typeWriter(botIndex, answer, sources, steps);
      },
      error: (err) => {
        console.error(err);
        this.messages.pop();
        this.errorMessage = err.status === 503 || err.status === 504 || err.status === 0
          ? 'Server waking up... Please wait a moment and retry.'
          : 'Unable to get an answer from the backend. Please try again.';
        this.isLoading = false;
      }
    });
  }

  // ✅ Reusable scroll function
  private typeWriter(index: number, text: string, sources: string[], steps: AgentStep[]) {
    let position = 0;
    const interval = window.setInterval(() => {
      if (!this.messages[index]) {
        window.clearInterval(interval);
        return;
      }

      this.messages[index].text += text.charAt(position);
      position += 1;
      this.scrollToBottom();

      if (position >= text.length) {
        window.clearInterval(interval);
        this.messages[index].isTyping = false;
        this.messages[index].sources = sources;
        this.messages[index].steps = steps;
        this.isLoading = false;
      }
    }, 16);
  }

  toggleSteps(message: ChatMessage) {
    message.expandSteps = !message.expandSteps;
  }

  scrollToBottom() {
    setTimeout(() => {
      if (this.chatBox) {
        this.chatBox.nativeElement.scrollTop =
          this.chatBox.nativeElement.scrollHeight;
      }
    }, 100);
  }
}