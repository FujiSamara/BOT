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
		<h2 class="title">{{ props.subDivision.name }}</h2>
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
</template>
<style scoped lang="scss">
.sub-division {
	display: flex;
	flex-direction: column;

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
		font-family: Wix Madefor Display;
		font-weight: 600;
		font-size: 20px;
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
	}
}
</style>
