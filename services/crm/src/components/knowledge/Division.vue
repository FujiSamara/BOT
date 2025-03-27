<script setup lang="ts">
import { PropType } from "vue";

import SubDivision from "@/components/knowledge/SubDivision.vue";

import { KnowledgeDivision } from "@/components/knowledge";

const props = defineProps({
	division: {
		type: Object as PropType<KnowledgeDivision>,
		required: true,
	},
});

const emits = defineEmits<{
	(e: "click", index: number): void;
}>();
</script>
<template>
	<div class="kn-chapter">
		<span class="path">{{ props.division.path }}</span>
		<SubDivision
			v-for="(subDivision, index) in props.division.subdivisions"
			:key="subDivision.id"
			:sub-division="subDivision"
			@click.stop="emits('click', index)"
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
