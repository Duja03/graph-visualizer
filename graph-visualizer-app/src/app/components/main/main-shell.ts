import { Component } from '@angular/core';
import {Header} from './header/header';
import {SideNavigation} from './side-navigation/side-navigation';

@Component({
  selector: 'app-main',
  imports: [
    Header,
    SideNavigation
  ],
  templateUrl: './main-shell.html',
  styleUrl: './main-shell.css',
})
export class MainShell {

}
