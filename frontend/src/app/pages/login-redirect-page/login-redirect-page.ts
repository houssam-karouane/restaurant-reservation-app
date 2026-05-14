import { ChangeDetectionStrategy, Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

/** Keeps `/login` as the guard target while reusing the real login screen at `/auth/login`. */
@Component({
  selector: 'app-login-redirect-page',
  standalone: true,
  template: '',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LoginRedirectPage implements OnInit {
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);

  ngOnInit(): void {
    const q = this.route.snapshot.queryParams;
    void this.router.navigate(['/auth/login'], { queryParams: q, replaceUrl: true });
  }
}
