import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NavigationEnd, Router, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs/operators';

import { Header } from './components/header/header';
import { Footer } from './components/footer/footer';
import { Toast } from './components/atoms/toast/toast';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Header, Footer, Toast],
  templateUrl: './app.html',
  styleUrl: './app.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class App {
  private readonly router = inject(Router);

  /** CSS class toggled briefly after each completed navigation for a subtle enter animation. */
  readonly outletEnterClass = signal(false);

  private hasCompletedInitialNavigation = false;

  constructor() {
    this.router.events
      .pipe(
        filter((e): e is NavigationEnd => e instanceof NavigationEnd),
        takeUntilDestroyed(),
      )
      .subscribe(() => {
        if (!this.hasCompletedInitialNavigation) {
          this.hasCompletedInitialNavigation = true;
          return;
        }

        this.outletEnterClass.set(false);
        requestAnimationFrame(() => {
          requestAnimationFrame(() => this.outletEnterClass.set(true));
        });
        window.setTimeout(() => this.outletEnterClass.set(false), 360);
      });
  }
}
