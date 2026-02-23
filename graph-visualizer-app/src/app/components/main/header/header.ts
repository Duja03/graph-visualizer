import {Component} from '@angular/core';
import {shared} from '../../../app.config';
import {Router} from '@angular/router';
import {MatSlideToggleChange} from '@angular/material/slide-toggle';
import { NgOptimizedImage } from '@angular/common';


@Component({
  selector: 'app-header',
  imports: [
    shared,
    NgOptimizedImage
  ],
  templateUrl: './header.html',
  styleUrl: './header.css',
})
export class Header {

  constructor(private router: Router) {
  }

  onToggleChange(event: MatSlideToggleChange) {
    console.log('Toggled to:', event.checked ? 'BlockView' : 'Simple View');
  }

  navigateToHome() {
    this.router.navigate(['/']);
  }
}
