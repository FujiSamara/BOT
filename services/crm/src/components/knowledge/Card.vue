<script setup lang="ts">
import { computed, PropType } from "vue";

import DishCardView from "@/components/knowledge/DishCard.vue";
import CommonCard from "@/components/knowledge/CommonCard.vue";

import { Card, CardType, DishCard, BusinessCard } from "@/components/knowledge";

const props = defineProps({
	path: {
		type: String,
		required: true,
	},
	card: {
		type: Object as PropType<Card>,
		required: true,
	},
});

const dish = computed(() => props.card as DishCard);
const business = computed(() => props.card as BusinessCard);
</script>
<template>
	<div class="k-card">
		<span class="path">{{ path }}</span>
		<DishCardView
			v-if="props.card.type == CardType.dish"
			:key="props.card.id"
			:card="dish"
		></DishCardView>
		<CommonCard v-else :card="business"></CommonCard>
	</div>
</template>
<style scoped lang="scss">
.k-card {
	display: flex;
	flex-direction: column;

	width: 100%;
	height: fit-content;
	gap: 32px;
}
</style>
