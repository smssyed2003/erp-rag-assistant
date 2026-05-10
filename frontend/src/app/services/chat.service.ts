import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

export interface ChatResponse {
  answer: string;
  sources: string[];
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private API_URL = `${environment.backendUrl}/ask`;

  constructor(private http: HttpClient) {}

  askQuestion(question: string, sessionId: string): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(this.API_URL, {
      question,
      session_id: sessionId
    });
  }
}
