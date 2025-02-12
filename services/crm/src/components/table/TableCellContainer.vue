<script setup lang="ts">
import {
	nextTick,
	onMounted,
	onUnmounted,
	PropType,
	ref,
	useTemplateRef,
} from "vue";

import TableCell from "@/components/table/TableCell.vue";

import { Cell } from "@/components/table";

const props = defineProps({
	cell: {
		type: Object as PropType<Cell>,
	},
	photoDisabled: {
		type: Boolean,
	},
});
const emits = defineEmits(["photoOpen", "photoClose"]);

const cellWrapperRef = useTemplateRef("cellWrapper");
const hintRef = useTemplateRef("hint");

const hintVisible = ref(false);
const hintAvailable = ref(false);

const resizeHint = () => {
	if (!hintRef.value) {
		return;
	}

	const element = hintRef.value;

	const maxGrantedWidth = parseInt(
		window
			.getComputedStyle(document.documentElement)
			.getPropertyValue("--max-hint-width"),
	);

	window.getComputedStyle(element).opacity; // Force dom to rerender component.
	element.style.width = "max-content";
	window.getComputedStyle(element).opacity; // Force dom to rerender component.

	if (element.offsetWidth > maxGrantedWidth) {
		element.style.width = `${maxGrantedWidth}px`;
	}
};

const checkOverflow = () => {
	if (!cellWrapperRef.value) {
		return;
	}

	const cellElement = (cellWrapperRef.value as HTMLElement)
		.children[0] as HTMLElement;
	hintAvailable.value =
		cellElement.scrollHeight > cellElement.offsetHeight ||
		cellElement.scrollWidth > cellElement.offsetWidth;
};
const observer = new MutationObserver(checkOverflow);

const mouseEnter = async () => {
	if (!hintAvailable.value) {
		return;
	}

	if (!hintRef.value || !cellWrapperRef.value) {
		return;
	}

	const hint = hintRef.value as HTMLElement;
	const cellWrapper = cellWrapperRef.value as HTMLElement;

	hintVisible.value = true;

	await nextTick();
	resizeHint();

	const rect = cellWrapper.getBoundingClientRect();

	let top = rect.top + rect.height - hint.offsetHeight;
	if (top < 0) {
		top = 0;
	}
	hint.style.top = `${top}px`;
	hint.style.left = `${rect.left - hint.offsetWidth}px`;
};

onMounted(() => {
	if (cellWrapperRef.value) {
		observer.observe(cellWrapperRef.value, { attributes: true });
	}
});

onUnmounted(() => {
	observer.disconnect();
});
</script>

<template>
	<div
		class="cell-wrapper"
		ref="cellWrapper"
		@mouseenter="mouseEnter"
		@mouseleave="hintVisible = false"
		:class="{ highlight: hintAvailable }"
	>
		<TableCell
			class="cell"
			:cell="props.cell"
			:photo-disabled="props.photoDisabled"
			@photo-close="emits('photoClose')"
			@photo-open="emits('photoOpen')"
		>
			<slot></slot>
		</TableCell>
		<Transition name="fade">
			<div ref="hint" class="hint" v-show="hintAvailable && hintVisible">
				<TableCell
					:cell="props.cell"
					:photo-disabled="props.photoDisabled"
					@photo-close="emits('photoClose')"
					@photo-open="emits('photoOpen')"
				>
					<slot></slot>
				</TableCell>
			</div>
		</Transition>
	</div>
</template>

<style scoped lang="scss">
.cell-wrapper {
	display: flex;
	flex-direction: column;
	align-items: flex-start;

	max-height: 100%;
	height: 100%;
	min-height: 100%;
	max-width: var(--max-cell-width);

	position: relative;
	background-color: transparent;

	&.highlight {
		background-color: $bg-accent-blue-3;
	}

	.hint {
		display: flex;
		flex-direction: column;
		align-items: center;
		position: fixed;

		max-height: 300px;
		width: var(--max-hint-width);

		z-index: 2;
		border-radius: 8px;
		border: 1px $stroke-gray solid;
		padding: 16px;
		background-color: $main-white;
		box-shadow: 0px 6px 16px 0px rgba(0, 0, 0, 0.1);

		.cell {
			overflow: auto;
			max-width: 100%;
			max-height: 100%;
		}
	}

	.cell {
		overflow: hidden;
		width: 100%;
		height: 100%;
	}
}
</style>
