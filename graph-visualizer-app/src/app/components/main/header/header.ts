import {Component} from '@angular/core';
import {shared} from '../../../app.config';
import {Router} from '@angular/router';


@Component({
  selector: 'app-header',
  imports: [
    shared
  ],
  templateUrl: './header.html',
  styleUrl: './header.css',
})
export class Header {

  constructor(private router: Router) {
  }

  navigateToHome() {
    this.router.navigate(['/']);
  }
}
