import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

export interface ChatResponse {
  answer: string;
  sources: any[];
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private http = inject(HttpClient);

  private API_URL = `${environment.backendUrl}/agent-ask`;

  askQuestion(question: string, sessionId: string): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(this.API_URL, {
      question,
      session_id: sessionId
    });
  }
}