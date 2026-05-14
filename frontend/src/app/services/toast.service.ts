import { Injectable, signal } from '@angular/core';

export type ToastVariant = 'success' | 'error' | 'info';

export interface Toast {
  id: number;
  message: string;
  variant: ToastVariant;
}

@Injectable({ providedIn: 'root' })
export class ToastService {
  private readonly _toasts = signal<Toast[]>([]);
  readonly toasts = this._toasts.asReadonly();

  private nextId = 1;
  private readonly defaultDurationMs = 4000;

  success(message: string, durationMs = this.defaultDurationMs): void {
    this.push(message, 'success', durationMs);
  }

  error(message: string, durationMs = this.defaultDurationMs): void {
    this.push(message, 'error', durationMs);
  }

  info(message: string, durationMs = this.defaultDurationMs): void {
    this.push(message, 'info', durationMs);
  }

  dismiss(id: number): void {
    this._toasts.update((current) => current.filter((t) => t.id !== id));
  }

  private push(message: string, variant: ToastVariant, durationMs: number): void {
    const id = this.nextId++;
    this._toasts.update((current) => [...current, { id, message, variant }]);
    if (durationMs > 0 && typeof window !== 'undefined') {
      window.setTimeout(() => this.dismiss(id), durationMs);
    }
  }
}
