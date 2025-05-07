import { nextTick, Ref, ref, ShallowRef, watch } from "vue";
import { toast } from "vue3-toastify";

import {
	EventBus,
	PDFLinkService,
	PDFViewer,
} from "pdfjs-dist/web/pdf_viewer.mjs";
import { getDocument, GlobalWorkerOptions, PDFDocumentProxy } from "pdfjs-dist";

import pdfjsWorker from "pdfjs-dist/legacy/build/pdf.worker?url";
GlobalWorkerOptions.workerSrc = pdfjsWorker;

export const usePdfViewer = (
	container: ShallowRef<HTMLDivElement | null>,
	wrapper: ShallowRef<HTMLDivElement | null>,
	expanded: Ref<boolean>,
) => {
	let pdfViewer: PDFViewer;
	let document: PDFDocumentProxy;
	let eventBus: EventBus | null = null;
	let destroyEventBus = () => {};
	let waitRender = async () => {};

	const ready = ref(true);
	let needRender = false;

	const loadFile = async (url: string) => {
		ready.value = false;
		document = await getDocument(url).promise;
		ready.value = true;
	};

	const init = async () => {
		if (pdfViewer) {
			toast.error("Вьюер уже инициализирован.", { delay: 1000 });
			return;
		}

		if (!document || !container.value) {
			return;
		}

		eventBus = new EventBus();

		const linkService = new PDFLinkService({ eventBus });
		pdfViewer = new PDFViewer({
			container: container.value,
			eventBus,
			linkService,
			removePageBorders: true,
		});
		const { destroy, waitInit, waitPageRender } = useEventHandling(eventBus);
		destroyEventBus = destroy;
		waitRender = waitPageRender;

		linkService.setViewer(pdfViewer);
		linkService.setDocument(document, null);

		pdfViewer.setDocument(document);

		await waitInit();

		tryResize();
		runRenderLoop();
	};

	const resize = async () => {
		if (!pdfViewer) {
			toast.error("Вьюер еще не инициализирован.", { delay: 1000 });
			return;
		}

		await nextTick();

		if (!container.value || !wrapper.value) {
			return;
		}

		const viewerEl = container.value?.querySelector(
			".pdfViewer",
		) as HTMLElement;
		if (!viewerEl) return;

		const width = viewerEl.firstElementChild!.scrollWidth;
		const availableWidth = wrapper.value.offsetWidth;

		const scale = availableWidth / width;

		const fullHeight = viewerEl.scrollHeight * scale;
		const firstPageHeight =
			viewerEl.firstElementChild!.scrollHeight * scale || 480;

		if (expanded.value) {
			wrapper.value.style.height = `${fullHeight}px`;
		} else {
			const height = Math.min(480, firstPageHeight);

			wrapper.value.style.height = `${height}px`;
		}

		await nextTick();

		pdfViewer.currentScale *= scale;
	};

	const runRenderLoop = async () => {
		for (;;) {
			if (needRender) {
				needRender = false;
				await resize();
				await waitRender();
			}
			await new Promise((resolve) => setTimeout(resolve, 100));
		}
	};

	const tryResize = async () => {
		needRender = true;
	};

	watch(expanded, resize);

	const destroy = () => {
		if (pdfViewer) {
			destroyEventBus();
			pdfViewer.cleanup();
		}
	};

	return {
		ready,
		loadFile,
		init,
		destroy,
		tryResize,
	};
};

const useEventHandling = (eventBus: EventBus) => {
	let initResolve = () => {};
	const initPromise = new Promise<void>((resolve) => {
		initResolve = resolve;
	});
	let renderResolve = () => {};
	let renderPromise = new Promise<void>((resolve) => {
		renderResolve = resolve;
	});

	const onPageInit = () => {
		initResolve();
	};
	eventBus.on("pagesinit", onPageInit);

	const onPageRender = () => {
		renderResolve();
		renderPromise = new Promise<void>((resolve) => {
			renderResolve = resolve;
		});
	};
	eventBus.on("pagerendered", onPageRender);

	const destroy = () => {
		eventBus.off("pagesinit", onPageInit);
		eventBus.off("pagerendered", onPageRender);
	};

	return {
		waitInit: async () => await initPromise,
		waitPageRender: async () => await renderPromise,
		destroy,
	};
};
