<script setup lang="ts">
import { PropType } from "vue";

import SubDivision from "@/components/knowledge/SubDivision.vue";

import { KnowledgeChapter } from "@/components/knowledge";

const props = defineProps({
	chapter: {
		type: Object as PropType<KnowledgeChapter>,
		required: true,
	},
});
</script>
<template>
	<div class="kn-chapter">
		<span class="path">{{ props.chapter.path }}</span>
		<SubDivision
			v-for="subDivision in props.chapter.children"
			:sub-division="subDivision"
		></SubDivision>
	</div>
</template>
<style scoped lang="scss">
.kn-chapter {
	display: flex;
	flex-direction: column;

	gap: 32px;
	padding: 32px;

	width: 100%;
	height: fit-content;

	background-color: $main-white;
	border-radius: 16px;

	.path {
		font-family: Wix Madefor Display;
		font-weight: 500;
		font-size: 16px;
	}
}
</style>
