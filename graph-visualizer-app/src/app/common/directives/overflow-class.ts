import { AfterViewChecked, AfterViewInit, Directive, ElementRef, Input } from '@angular/core';

@Directive({
  selector: '[overflowClass]',
  standalone: true
})
export class OverflowClass implements AfterViewInit, AfterViewChecked {

  @Input() overflowClass: string | null = null;

  constructor(private el: ElementRef) {
  }

  ngAfterViewInit(): void {
    this.checkScroll();
  }

  ngAfterViewChecked(): void {
    this.checkScroll();
  }

  private checkScroll() {
    const overflowClasses = this.overflowClass?.split(' ');
    (overflowClasses?.length ? overflowClasses : [this.overflowClass]).forEach((cssClass) => {
      if (this.el.nativeElement.scrollHeight > this.el.nativeElement.clientHeight) {
        this.el.nativeElement.classList.add(cssClass);
      } else {
        this.el.nativeElement.classList.remove(cssClass);
      }
    })
  }
}
