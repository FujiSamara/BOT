<script setup lang="ts">
import { computed, PropType } from "vue";

import { FileLinkSchema } from "@/components/knowledge/types";
import { formatDate } from "@/parser";

const props = defineProps({
	materials: {
		type: Array as PropType<FileLinkSchema[]>,
		required: true,
	},
});

const materials = computed(() => props.materials);
const downloadClicked = (url: string) => {
	window.open(url, "_blanc")!.focus();
};
</script>
<template>
	<div class="c-materials-wrapper">
		<div class="c-materials">
			<span>Материалы</span>
			<ul>
				<li v-for="material in materials">
					<span class="title">
						{{ material.name }}
					</span>
					<div class="meta">
						<span>{{ formatDate(material.created) }}</span>
						<span>{{ material.size / 1e6 }} MB</span>
						<button @click="downloadClicked(material.url)" class="download">
							Скачать
						</button>
					</div>
				</li>
			</ul>
		</div>
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
				}

				.meta {
					display: flex;
					flex-direction: row;
					align-items: center;
					gap: 24px;

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
