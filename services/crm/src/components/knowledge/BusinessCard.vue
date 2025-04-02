<script setup lang="ts">
import { PropType } from "vue";
import PulseSpinner from "@/components/UI-new/PulseSpinner.vue";
import CardMaterials from "./CardMaterials.vue";
import { BusinessCard } from "@/components/knowledge";

const props = defineProps({
	card: {
		type: Object as PropType<BusinessCard>,
		required: true,
	},
});
</script>
<template>
	<div class="card-wrapper">
		<header>
			<h2 class="title">{{ props.card.name }}</h2>
			<span class="description">{{ props.card.description }}</span>
		</header>

		<Transition name="fade" mode="out-in">
			<footer v-if="props.card.materials !== undefined" class="materials">
				<div class="main-document"></div>
				<CardMaterials :materials="props.card.materials"></CardMaterials>
			</footer>
			<div v-else class="spinner-wrapper">
				<PulseSpinner class="spinner"></PulseSpinner>
			</div>
		</Transition>
	</div>
</template>
<style scoped lang="scss">
@import url("./style.scss");

.card-wrapper {
	header {
		display: flex;
		flex-direction: column;

		width: 100%;
		height: fit-content;

		gap: 36px;
	}
}
</style>
