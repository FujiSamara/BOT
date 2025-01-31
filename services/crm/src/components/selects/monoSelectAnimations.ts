import gsap from "gsap";

function getDelay(index: number): number {
	const delayCount = 4;

	if (index < delayCount) {
		return index * 0.15;
	}
	return delayCount * 0.15;
}

export function onBeforeEnter(el: any) {
	el.style.opacity = 0;
	el.style.height = 0;
	el.style.marginTop = 0;
	el.style.paddingTop = 0;
	el.style.paddingBottom = 0;
	el.style.overflow = "hidden";
}

export function onEnter(el: any, done: any) {
	gsap.to(el, {
		opacity: 1,
		marginTop: "4px",
		paddingTop: "8px",
		paddingBottom: "8px",
		height: "26px",
		delay: getDelay(el.dataset.index),
		onComplete: done,
	});
}

export function onLeave(el: any, done: any) {
	gsap.to(el, {
		opacity: 0,
		height: 0,
		paddingTop: 0,
		marginTop: 0,
		paddingBottom: 0,
		delay: getDelay(el.dataset.index),
		onComplete: done,
	});
}
