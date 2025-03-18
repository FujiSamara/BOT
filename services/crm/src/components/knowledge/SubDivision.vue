<script setup lang="ts">
import { PropType } from "vue";
import { KnowledgeDivision, KnowledgeChapter } from "@/components/knowledge";

const props = defineProps({
	subDivision: {
		type: Object as PropType<KnowledgeDivision>,
		required: true,
	},
});

const asChapter = props.subDivision as KnowledgeChapter;
const isChapter = props.subDivision.type === "chapter";
</script>
<template>
	<div class="sub-division">
		<h2 class="title">{{ props.subDivision.title }}</h2>
		<ul class="cards" v-if="isChapter && asChapter.children.length">
			<li
				v-for="card in asChapter.children.filter((val) => val.type === 'card')"
			>
				{{ card.title }}
			</li>
		</ul>
		<div class="meta">
			<span v-if="isChapter">{{ asChapter.childrenCount }} статьи</span>
			<span>•</span>
			<span>{{ props.subDivision.filesCount }} файлов</span>
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
