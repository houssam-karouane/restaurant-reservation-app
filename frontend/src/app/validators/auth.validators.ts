import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

export class AuthValidators {
  static emailValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      if (!control.value) {
        return null;
      }

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      const valid = emailRegex.test(control.value);
      return valid ? null : { invalidEmail: true };
    };
  }

  static passwordValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      if (!control.value) {
        return null;
      }

      const value = control.value;
      if (value.length < 8) {
        return { passwordTooShort: true };
      }

      return null;
    };
  }

  static passwordMatchValidator(passwordField: string, confirmPasswordField: string): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      const password = control.get(passwordField);
      const confirmPassword = control.get(confirmPasswordField);

      if (!password || !confirmPassword) {
        return null;
      }

      return password.value === confirmPassword.value ? null : { passwordMismatch: true };
    };
  }
}
