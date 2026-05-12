import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment';

interface Stats {
  uptime_seconds: number;
  total_requests: number;
  failed_requests: number;
  error_rate_percent: number;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="space-y-8">
      <div class="flex items-center justify-between">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Monitoring Dashboard</h1>
        <button (click)="loadStats()" class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors shadow-sm">
          Refresh
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <!-- Health -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-3 h-3 rounded-full" [class.bg-green-500]="health()" [class.bg-red-500]="!health()"></div>
            <span class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">System Health</span>
          </div>
          <p class="text-2xl font-black" [class.text-green-600]="health()" [class.text-red-600]="!health()">{{ health() ? 'Healthy' : 'Unhealthy' }}</p>
        </div>

        <!-- Uptime -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
          <div class="flex items-center gap-3 mb-4">
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <span class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Uptime</span>
          </div>
          <p class="text-2xl font-black text-gray-900 dark:text-white">{{ formatUptime(stats()?.uptime_seconds) }}</p>
        </div>

        <!-- Total Requests -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
          <div class="flex items-center gap-3 mb-4">
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>
            <span class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Total Requests</span>
          </div>
          <p class="text-2xl font-black text-gray-900 dark:text-white">{{ stats()?.total_requests || 0 }}</p>
        </div>

        <!-- Error Rate -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
          <div class="flex items-center gap-3 mb-4">
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path></svg>
            <span class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Error Rate</span>
          </div>
          <p class="text-2xl font-black" [class.text-green-600]="(stats()?.error_rate_percent || 0) < 5" [class.text-orange-500]="(stats()?.error_rate_percent || 0) >= 5" [class.text-red-600]="(stats()?.error_rate_percent || 0) >= 20">{{ stats()?.error_rate_percent || 0 }}%</p>
          <p class="text-sm text-gray-400 mt-1">{{ stats()?.failed_requests || 0 }} failed</p>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
        <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4">Recent Error Logs</h2>
        @if (logs().length === 0) {
          <p class="text-gray-500 dark:text-gray-400 text-sm">No recent errors. The system is running smoothly.</p>
        } @else {
          <div class="space-y-2">
            @for (log of logs(); track log) {
              <div class="text-sm font-mono bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 p-3 rounded-lg">{{ log }}</div>
            }
          </div>
        }
      </div>
    </div>
  `
})
export class DashboardComponent implements OnInit {
  private http = inject(HttpClient);

  stats = signal<Stats | undefined>(undefined);
  health = signal(false);
  logs = signal<string[]>([]);

  ngOnInit() {
    this.loadStats();
  }

  loadStats() {
    this.http.get<Stats>(`${environment.apiUrl}/stats`).subscribe({
      next: (s) => this.stats.set(s)
    });

    this.http.get<{ status: string }>(`${environment.apiUrl}/health`).subscribe({
      next: (h) => this.health.set(h.status === 'healthy')
    });

    this.http.get<string[]>(`${environment.apiUrl}/stats/recent-errors`).subscribe({
      next: (l) => this.logs.set(l),
      error: () => {}
    });
  }

  formatUptime(seconds?: number): string {
    if (!seconds) return '0s';
    const d = Math.floor(seconds / 86400);
    const h = Math.floor((seconds % 86400) / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    const parts: string[] = [];
    if (d > 0) parts.push(`${d}d`);
    if (h > 0) parts.push(`${h}h`);
    if (m > 0) parts.push(`${m}m`);
    parts.push(`${s}s`);
    return parts.join(' ');
  }
}
