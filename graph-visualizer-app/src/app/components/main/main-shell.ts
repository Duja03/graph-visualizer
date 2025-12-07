import { Component } from '@angular/core';
import {Header} from './header/header';

@Component({
  selector: 'app-main',
  imports: [
    Header
  ],
  templateUrl: './main-shell.html',
  styleUrl: './main-shell.css',
})
export class MainShell {

}
