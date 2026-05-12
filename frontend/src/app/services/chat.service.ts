import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface ChatResponse {
  answer: string;
  sources: string[];
}

@Injectable()
export class ChatService {
  private API_URL = `${environment.backendUrl}/ask`;
  private http = inject(HttpClient);

  askQuestion(question: string, sessionId: string): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(this.API_URL, {
      question,
      session_id: sessionId
    });
  }
}