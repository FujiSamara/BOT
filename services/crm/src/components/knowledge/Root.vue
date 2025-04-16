<script setup lang="ts">
import { computed, PropType } from "vue";

import SubDivision from "@/components/knowledge/SubDivision.vue";
import PulseSpinner from "@/components/UI-new/PulseSpinner.vue";

import { KnowledgeRootDivision } from "@/components/knowledge/types";

const props = defineProps({
	divisions: {
		type: Array as PropType<KnowledgeRootDivision[]>,
	},
});

const emits = defineEmits<{
	(e: "click", index: number): void;
}>();

const divisions = computed(() => props.divisions);
</script>
<template>
	<Transition>
		<div class="kn-root" v-if="divisions !== undefined">
			<span class="path">База знаний</span>
			<div class="kn-chapter">
				<SubDivision
					v-for="(division, index) in divisions"
					:key="division.id"
					:sub-division="division"
					:icon="division.iconURL"
					:title-size="'36px'"
					@click.stop="emits('click', index)"
					class="card"
				></SubDivision>
			</div>
		</div>

		<div v-else class="spinner-wrapper">
			<PulseSpinner class="spinner"></PulseSpinner>
		</div>
	</Transition>
</template>
<style scoped lang="scss">
.kn-root {
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
		font-weight: 400;
		font-size: 16px;
	}
	.kn-chapter {
		display: flex;
		flex-direction: row;

		flex-wrap: wrap;

		gap: 20px;

		.card {
			display: flex;
			flex-grow: 1;

			padding-top: 36px;

			width: 480px;
			height: 200px;

			border: none;
		}
	}
}
</style>
