<script setup lang="ts">
import { PropType, Ref, ref } from "vue";
import DocumentView from "@/components/DocumentView.vue";

import { Cell, CellLine } from "@/components/table";
import { useNetworkStore } from "@/store/network";
import { DocumentSchema } from "@/types";

const props = defineProps({
	cell: {
		type: Object as PropType<Cell>,
	},
	photoDisabled: {
		type: Boolean,
	},
});
const emits = defineEmits(["photoOpen", "photoClose"]);

const networkStore = useNetworkStore();

const documentViewVisible = ref(false);
const documents: Ref<Array<DocumentSchema>> = ref([]);
const initialDocumentIndex: Ref<number> = ref(1);

const linkClicked = async (cellLine: CellLine) => {
	if (cellLine.forceHref) {
		await networkStore.downloadFile(cellLine.value, cellLine.href);
	} else {
		await networkStore.downloadFile(cellLine.value);
	}
};

const openPhoto = (cell: Cell, index: number) => {
	if (props.photoDisabled) {
		return;
	}

	const docs: Array<DocumentSchema> = [];
	for (const [i, cellLine] of cell.cellLines.entries()) {
		if (cellLine.isImage) {
			if (index === i) {
				initialDocumentIndex.value = docs.length;
			}
			docs.push({ name: cellLine.value, href: cellLine.href, forceHref: true });
		}
	}
	emits("photoOpen");
	documentViewVisible.value = true;
	documents.value = docs;
};
</script>

<template>
	<div class="cell">
		<slot v-if="!props.cell"></slot>
		<ul class="cell-line-list" v-if="props.cell">
			<li
				class="cell-line"
				v-for="(cellLine, cellLineIndex) in props.cell.cellLines"
			>
				<div
					class="c-link-wrapper"
					:style="{ color: cellLine.color }"
					v-if="cellLine.href.length > 0"
				>
					<a
						@click.stop="async () => await linkClicked(cellLine)"
						class="c-link"
						>{{ cellLine.value }}</a
					>
					<div
						@click.stop="() => openPhoto(props.cell!, cellLineIndex)"
						v-if="cellLine.isImage"
						class="c-image"
						:class="{
							active: documentViewVisible,
							disabled: props.photoDisabled,
						}"
					></div>
				</div>
				<p :style="{ color: cellLine.color }" v-if="cellLine.href.length === 0">
					{{ cellLine.value }}
				</p>
			</li>
		</ul>

		<Suspense>
			<Transition name="fade">
				<DocumentView
					v-if="documentViewVisible"
					:documents="documents"
					:index="initialDocumentIndex"
					@close="
						documentViewVisible = false;
						emits('photoClose');
					"
				></DocumentView>
			</Transition>
		</Suspense>
	</div>
</template>

<style scoped lang="scss">
.cell {
	margin: auto 0;

	.cell-line-list {
		display: flex;
		flex-direction: column;
		gap: 4px;

		list-style: none;
		margin: 0;
		padding: 0;

		.cell-line {
			p {
				margin: 0;
				cursor: default;
			}

			.c-link-wrapper {
				display: flex;
				align-items: center;
				gap: 8px;
				cursor: default;

				.c-link {
					color: $main-accent-blue;
					transition: color 0.25s;
					text-decoration: underline;
					user-select: none;
					cursor: pointer;
					transition: color 0.25s;

					&:hover {
						color: $main-dark-gray;
					}
				}

				.c-image {
					background-color: currentColor;
					color: $main-dark-gray;
					width: 20px;
					height: 20px;
					fill: currentColor;

					mask-size: contain;
					mask-image: url("@/assets/icons/image.svg");
					mask-repeat: no-repeat;

					transition: color 0.25s;

					&:hover {
						color: $main-accent-blue;
						cursor: pointer;
					}

					&.disabled {
						color: $sec-dark-gray-25;
						cursor: default;
					}

					&.active {
						color: $sec-accent-blue-50;
					}
				}
			}
		}
	}
}
</style>
