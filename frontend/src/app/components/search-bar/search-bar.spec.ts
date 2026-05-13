import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';

import { SearchBar } from './search-bar';

describe('SearchBar', () => {
  describe('live updates (default)', () => {
    let fixture: ComponentFixture<SearchBar>;

    beforeEach(async () => {
      await TestBed.configureTestingModule({
        imports: [SearchBar],
      }).compileComponents();

      fixture = TestBed.createComponent(SearchBar);
      fixture.componentRef.setInput('initialFilters', {
        city: '',
        cuisine: '',
        priceRange: null,
        minRating: null,
      });
      fixture.detectChanges();
    });

    it('should create', () => {
      expect(fixture.componentInstance).toBeTruthy();
    });

    it('should emit filtersChange when a filter changes', fakeAsync(() => {
      const spy = jest.fn();
      fixture.componentInstance.filtersChange.subscribe(spy);

      fixture.componentInstance.form.patchValue({ cuisine: 'japonaise' });
      tick(200);

      expect(spy).toHaveBeenCalled();
      const last = spy.mock.calls[spy.mock.calls.length - 1][0] as {
        city: string;
        cuisine: string;
        priceRange: number | null;
        minRating: number | null;
      };
      expect(last.cuisine).toBe('japonaise');
    }));
  });

  describe('submitOnly', () => {
    let fixture: ComponentFixture<SearchBar>;

    beforeEach(async () => {
      await TestBed.configureTestingModule({
        imports: [SearchBar],
      }).compileComponents();

      fixture = TestBed.createComponent(SearchBar);
      fixture.componentRef.setInput('initialFilters', {
        city: '',
        cuisine: '',
        priceRange: null,
        minRating: null,
      });
      fixture.componentRef.setInput('submitOnly', true);
      fixture.detectChanges();
    });

    it('should emit filtersChange on Search when submitOnly is true', () => {
      const spy = jest.fn();
      fixture.componentInstance.filtersChange.subscribe(spy);

      fixture.componentInstance.form.patchValue({ city: 'Lyon' });
      expect(spy).not.toHaveBeenCalled();

      const btn: HTMLButtonElement = fixture.nativeElement.querySelector(
        'button[type="submit"]',
      ) as HTMLButtonElement;
      btn.click();
      fixture.detectChanges();

      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy.mock.calls[0][0].city).toBe('Lyon');
    });
  });
});
