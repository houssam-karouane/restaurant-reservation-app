import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ProfileInfoComponent } from '../../components/profile/profile-info.component';
import { ReservationHistoryComponent } from '../../components/profile/reservation-history.component';
import { FavoritesComponent } from '../../components/profile/favorites.component';
import { RecommendationsComponent } from '../../components/profile/recommendations.component';

@Component({
  selector: 'app-profile-page',
  standalone: true,
  imports: [
    CommonModule,
    ProfileInfoComponent,
    ReservationHistoryComponent,
    FavoritesComponent,
    RecommendationsComponent,
  ],
  templateUrl: './profile-page.html',
  styleUrl: './profile-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProfilePage {}
