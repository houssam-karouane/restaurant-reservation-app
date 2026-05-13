import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';

import { SearchBar } from './search-bar';

describe('SearchBar', () => {
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
