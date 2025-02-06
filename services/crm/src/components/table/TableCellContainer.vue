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

const checkOverflow = () => {
	if (!cellWrapperRef.value) {
		return;
	}

	const element = (cellWrapperRef.value as HTMLElement)
		.children[0] as HTMLElement;
	hintAvailable.value = element.scrollHeight > element.offsetHeight;
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
	const cellParent = cellWrapper.parentElement as HTMLElement;

	hint.style.right = "100%";
	hintVisible.value = true;

	await nextTick();
	const rect = hint.getBoundingClientRect();

	if (rect.left < cellParent.offsetLeft) {
		hint.style.right = `calc(100% - ${cellParent.offsetLeft - rect.left}px)`;
	}
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
		position: absolute;

		bottom: 0;
		right: 100%;

		display: flex;
		flex-direction: column;
		align-items: flex-start;
		width: fit-content;

		white-space: nowrap;

		z-index: 2;
		border-radius: 8px;
		border: 1px $stroke-gray solid;
		padding: 16px;
		background-color: $main-white;
		box-shadow: 0px 6px 16px 0px rgba(0, 0, 0, 0.1);

		.cell {
			max-width: max-content;
		}
	}

	.cell {
		overflow: hidden;
		max-width: 100%;
		max-height: 100%;
	}
}
</style>
