import { Component, signal, OnInit, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { initFlowbite } from 'flowbite';
import { AuthService } from './core/services/auth.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  private authService = inject(AuthService);
  protected readonly title = signal('library-system');

  ngOnInit(): void {
    this.authService.init();
    try {
      initFlowbite();
    } catch (e) {
      console.warn('Flowbite initialization failed', e);
    }
  }
}
