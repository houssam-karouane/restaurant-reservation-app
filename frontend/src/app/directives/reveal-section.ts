import { isPlatformBrowser } from '@angular/common';
import {
  afterNextRender,
  Directive,
  ElementRef,
  inject,
  PLATFORM_ID,
  Renderer2,
} from '@angular/core';

/**
 * Adds `reveal-section--visible` when the host enters the viewport (calm fade + slide up).
 */
@Directive({
  selector: '[appRevealSection]',
  host: { class: 'reveal-section' },
})
export class RevealSectionDirective {
  private readonly el = inject(ElementRef<HTMLElement>);
  private readonly renderer = inject(Renderer2);
  private readonly platformId = inject(PLATFORM_ID);

  constructor() {
    afterNextRender(() => {
      if (!isPlatformBrowser(this.platformId)) {
        this.renderer.addClass(this.el.nativeElement, 'reveal-section--visible');
        return;
      }

      const node = this.el.nativeElement;
      const io = new IntersectionObserver(
        (entries) => {
          for (const e of entries) {
            if (e.isIntersecting) {
              this.renderer.addClass(node, 'reveal-section--visible');
              io.disconnect();
            }
          }
        },
        { threshold: 0.12, rootMargin: '0px 0px -32px 0px' },
      );
      io.observe(node);
    });
  }
}
