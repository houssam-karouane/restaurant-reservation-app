import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-inline-alert',
  imports: [CommonModule],
  templateUrl: './inline-alert.html',
  styleUrl: './inline-alert.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class InlineAlert {
  @Input({ required: true }) message!: string;
}
