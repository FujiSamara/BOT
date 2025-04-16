<script setup lang="ts">
import { computed, PropType } from "vue";

import {
	KnowledgeSubdivision,
	DivisionType,
} from "@/components/knowledge/types";

const props = defineProps({
	subDivision: {
		type: Object as PropType<KnowledgeSubdivision>,
		required: true,
	},
	icon: {
		type: String,
	},
	titleSize: {
		type: String,
	},
});

const cards = computed(() => [] as KnowledgeSubdivision[]);

const pluralizeExpenditure = (count: number) => {
	if (count === 1) return "Статья";
	if (count > 1 && count < 5) return "Статьи";
	return "Статей";
};
const pluralizeFiles = (count: number) => {
	if (count === 1) return "Файл";
	if (count > 1 && count < 5) return "Файла";
	return "Файлов";
};
</script>
<template>
	<div class="sub-division">
		<div class="title">
			<div
				class="icon"
				v-if="props.icon"
				:style="`mask: url(${props.icon}) no-repeat`"
			></div>
			<h2 class="title" :style="`font-size: ${props.titleSize}`">
				{{ props.subDivision.name }}
			</h2>
		</div>
		<div class="info">
			<ul class="cards" v-if="cards.length">
				<li v-for="card in cards">
					{{ card.name }}
				</li>
			</ul>
			<div class="meta">
				<span v-if="props.subDivision.type === DivisionType.division"
					>{{ props.subDivision.subdivisionsCount }}
					{{ pluralizeExpenditure(props.subDivision.subdivisionsCount) }}</span
				>
				<!-- <span v-if="props.subDivision.type == DivisionType.division">•</span> -->
				<span v-if="props.subDivision.type !== DivisionType.division"
					>{{ props.subDivision.filesCount }}
					{{ pluralizeFiles(props.subDivision.filesCount) }}</span
				>
			</div>
		</div>
	</div>
</template>
<style scoped lang="scss">
.sub-division {
	display: flex;
	flex-direction: column;
	justify-content: space-between;

	width: 100%;
	height: fit-content;

	gap: 16px;
	padding: 24px;

	border-radius: 16px;
	background-color: $bg-light-blue;

	transition: background-color 0.25s;
	cursor: default;

	&:hover {
		background-color: $sec-desktop-press;
	}

	.title {
		display: flex;
		flex-direction: row;
		align-items: center;

		gap: 12px;

		font-family: Wix Madefor Display;
		font-weight: 600;
		font-size: 20px;

		.icon {
			width: 23.67px;
			height: 23.67px;

			background-color: currentColor;
			fill: currentColor;
		}

		h2 {
			margin: 0;
		}
	}

	.cards {
		display: flex;
		flex-direction: row;
		flex-wrap: wrap;

		width: 100%;
		height: fit-content;
		gap: 16px;

		margin: 0;
		padding: 0;
		list-style: none;

		li:not(:last-child) {
			margin-right: 16px;
		}
	}

	.meta {
		display: flex;
		flex-direction: row;

		gap: 8px;

		opacity: 50%;
		color: $main-dark-gray;

		h2 {
			font-size: 36px;
		}
	}
}
</style>
