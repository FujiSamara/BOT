import gsap from "gsap";

export function onBeforeEnter(el: any) {
	el.style.opacity = 0;
	el.style.height = 0;
	el.style.overflow = "hidden";
}

export function onEnter(el: any, done: any) {
	gsap.to(el, {
		opacity: 1,
		height: "fit-content",
		clear: "padding",
		delay: el.dataset.index * 0.15,
		onComplete: done,
	});
}

export function onLeave(el: any, done: any) {
	gsap.to(el, {
		opacity: 0,
		height: 0,
		padding: 0,
		delay: el.dataset.index * 0.15,
		onComplete: done,
	});
}
