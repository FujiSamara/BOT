<script setup lang="ts">
import { computed, PropType, Ref, ref } from "vue";

import ImageView from "@/components/viewer/ImageView.vue";
import PulseSpinner from "@/components/UI-new/PulseSpinner.vue";
import DeleteButton from "@/components/UI-new/DeleteButton.vue";

import { imageExts } from "@/config";
import { FileLinkSchema } from "@/components/knowledge/types";
import { formatDate } from "@/parser";
import { DocumentSchema } from "@/types";

const props = defineProps({
	materials: {
		type: Array as PropType<FileLinkSchema[]>,
		required: true,
	},
	canDelete: {
		type: Boolean,
	},
});
const emits = defineEmits<{
	(e: "delete", index: number): void;
}>();

const materials = computed(() => props.materials);

const documentViewVisible = ref(false);
const documentLoading = ref(false);
const documents: Ref<Array<DocumentSchema>> = ref([]);
const initialDocumentIndex: Ref<number> = ref(1);
const isImage = (name: string) => {
	const names = name.split(".");
	const ext = names[names.length - 1];

	return imageExts.includes(ext);
};
const images = computed(() => {
	return materials.value.filter((val) => isImage(val.name));
});

const openPhoto = (file: FileLinkSchema) => {
	if (documentLoading.value) return;
	if (!isImage(file.name)) return;
	documentLoading.value = true;

	const docs: Array<DocumentSchema> = [];
	for (const [i, image] of images.value.entries()) {
		if (image.id === file.id) {
			initialDocumentIndex.value = i;
		}
		docs.push({
			name: image.name,
			href: image.url,
			forceHref: true,
			raw: true,
		});
	}

	documentViewVisible.value = true;
	documents.value = docs;
};
const downloadClicked = (url: string) => {
	window.open(url, "_blanc")!.focus();
};
</script>
<template>
	<div class="c-materials-wrapper">
		<div class="c-materials">
			<span>Материалы</span>
			<ul>
				<li v-for="(material, index) in materials">
					<span
						class="title"
						@click="() => openPhoto(material)"
						:class="{ photo: isImage(material.name), loading: documentLoading }"
					>
						{{ material.name }}
					</span>
					<div class="meta">
						<Transition name="fade">
							<PulseSpinner
								class="spinner"
								v-if="documentLoading && isImage(material.name)"
							></PulseSpinner>
						</Transition>
						<span>{{ formatDate(material.created) }}</span>
						<span>{{ material.size / 1e6 }} MB</span>
						<button @click="downloadClicked(material.url)" class="download">
							Скачать
						</button>
						<DeleteButton
							v-if="props.canDelete"
							@click="emits('delete', index)"
						></DeleteButton>
					</div>
				</li>
			</ul>
		</div>
		<Transition name="fade">
			<ImageView
				v-if="documentViewVisible"
				:documents="documents"
				:index="initialDocumentIndex"
				@close="documentViewVisible = false"
				@ready="documentLoading = false"
			></ImageView>
		</Transition>
	</div>
</template>
<style scoped lang="scss">
.c-materials-wrapper {
	display: flex;
	flex-direction: column;

	gap: 32px;

	width: 100%;
	height: fit-content;

	border-radius: 16px;
	padding: 32px;

	background-color: $main-white;

	span {
		display: flex;
		flex-direction: row;
		align-items: center;

		height: 42px;

		font-family: Wix Madefor Display;
		font-weight: 500;
		font-size: 16px;
		color: $sec-gray-blue;
	}

	.c-materials {
		display: flex;
		flex-direction: row;
		width: 100%;

		gap: 32px;

		ul {
			display: flex;
			flex-direction: column;
			width: 100%;

			gap: 16px;

			li {
				display: flex;
				flex-direction: row;
				align-items: center;

				justify-content: space-between;

				.title {
					font-family: Wix Madefor Display;
					font-weight: 500;
					font-size: 16px;
					color: $main-dark-gray;
					transition: color 0.25s;

					&.photo {
						cursor: pointer;

						&.loading {
							color: $sec-dark-gray-25;
						}
					}
				}

				.meta {
					display: flex;
					flex-direction: row;
					align-items: center;
					gap: 24px;

					.spinner {
						height: 24px;
						width: 24px;
					}

					.download {
						background-color: $main-accent-blue;
						border: none;
						color: $main-white;
						font-family: Wix Madefor Display;
						font-weight: 400;
						font-size: 12px;

						padding: 12px 32px;
						border-radius: 4px;

						transition: transform 0.25s;
						&:hover {
							transform: scale(1.02);
						}
					}

					span {
						font-family: Wix Madefor Display;
						font-weight: 500;
						font-size: 14px;
						color: $sec-gray-blue;
					}
				}
			}
		}
	}

	.spinner-wrapper {
		display: flex;
		justify-content: center;
		align-items: center;

		width: 100%;
		height: 100%;

		.spinner {
			width: 84px;
			height: 84px;

			color: $main-accent-blue;
		}
	}
}
</style>
