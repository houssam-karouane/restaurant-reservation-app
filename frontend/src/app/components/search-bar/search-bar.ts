import {
  ChangeDetectionStrategy,
  Component,
  afterNextRender,
  DestroyRef,
  inject,
  output,
  input,
  effect,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { debounceTime } from 'rxjs';

import type { RestaurantSearchFilters } from '../../models/restaurant';

@Component({
  selector: 'app-search-bar',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './search-bar.html',
  styleUrl: './search-bar.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SearchBar {
  private readonly fb = inject(FormBuilder);
  private readonly destroyRef = inject(DestroyRef);

  /** When true, filters emit only on Search / Enter — use on the home hero. */
  readonly submitOnly = input(false);

  readonly initialFilters = input<RestaurantSearchFilters>({
    city: '',
    cuisine: '',
    priceRange: null,
    minRating: null,
  });

  readonly filtersChange = output<RestaurantSearchFilters>();

  readonly cuisineOptions: ReadonlyArray<{ value: string; label: string }> = [
    { value: '', label: 'Any cuisine' },
    { value: 'française', label: 'Française' },
    { value: 'japonaise', label: 'Japonaise' },
    { value: 'italienne', label: 'Italienne' },
    { value: 'mexicaine', label: 'Mexicaine' },
    { value: 'chinoise', label: 'Chinoise' },
    { value: 'méditerranéenne', label: 'Méditerranéenne' },
  ];

  readonly form = this.fb.nonNullable.group({
    city: [''],
    cuisine: [''],
    priceRange: [''],
    minRating: [''],
  });

  constructor() {
    effect(() => {
      const f = this.initialFilters();
      this.form.patchValue(
        {
          city: f.city,
          cuisine: f.cuisine,
          priceRange: f.priceRange != null ? String(f.priceRange) : '',
          minRating: f.minRating != null ? String(f.minRating) : '',
        },
        { emitEvent: false },
      );
    });

    afterNextRender(() => {
      if (this.submitOnly()) {
        return;
      }
      this.form.valueChanges
        .pipe(debounceTime(200), takeUntilDestroyed(this.destroyRef))
        .subscribe(() => this.emitFilters());
    });
  }

  onSubmit(): void {
    this.emitFilters();
  }

  private emitFilters(): void {
    const v = this.form.getRawValue();
    const priceRange = v.priceRange === '' ? null : Number(v.priceRange);
    const minRating = v.minRating === '' ? null : Number(v.minRating);
    this.filtersChange.emit({
      city: v.city.trim(),
      cuisine: v.cuisine.trim(),
      priceRange: Number.isFinite(priceRange) ? priceRange : null,
      minRating: Number.isFinite(minRating) ? minRating : null,
    });
  }
}
