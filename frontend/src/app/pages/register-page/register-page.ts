import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { AuthValidators } from '../../validators/auth.validators';

@Component({
  selector: 'app-register-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './register-page.html',
  styleUrl: './register-page.css',
})
export class RegisterPage implements OnInit {
  registerForm!: FormGroup;
  submitted = false;
  loading = false;
  errorMessage = '';

  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.initializeForm();
  }

  private initializeForm(): void {
    this.registerForm = this.formBuilder.group(
      {
        name: ['', [Validators.required, Validators.minLength(2)]],
        email: ['', [Validators.required, AuthValidators.emailValidator()]],
        password: ['', [Validators.required, AuthValidators.passwordValidator()]],
        confirmPassword: ['', Validators.required],
      },
      {
        validators: AuthValidators.passwordMatchValidator('password', 'confirmPassword'),
      }
    );
  }

  get f() {
    return this.registerForm.controls;
  }

  onSubmit(): void {
    this.submitted = true;
    this.errorMessage = '';

    if (this.registerForm.invalid) {
      return;
    }

    this.loading = true;

    const { name, email, password } = this.registerForm.value;

    this.authService.register({ name, email, password }).subscribe({
      next: () => {
        this.router.navigate(['/']);
      },
      error: (error) => {
        this.loading = false;
        this.errorMessage =
          error.error?.detail || 'Registration failed. Please try again.';
      },
    });
  }

  getErrorMessage(fieldName: string): string {
    const control = this.registerForm.get(fieldName);

    if (!control || !control.errors || !this.submitted) {
      return '';
    }

    if (control.hasError('required')) {
      return `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)} is required`;
    }

    if (control.hasError('invalidEmail')) {
      return 'Please enter a valid email address';
    }

    if (control.hasError('minlength')) {
      const minLength = control.getError('minlength').requiredLength;
      return `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)} must be at least ${minLength} characters`;
    }

    if (control.hasError('passwordTooShort')) {
      return 'Password must be at least 8 characters';
    }

    return '';
  }

  getFormErrorMessage(): string {
    if (this.registerForm.hasError('passwordMismatch') && this.submitted) {
      return 'Passwords do not match';
    }
    return '';
  }
}
