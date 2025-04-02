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
		<h2 class="title">{{ props.card.name }}</h2>
		<h2>В Разработке!!!</h2>
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
}
</style>
