<script setup lang="ts">
import { PropType } from "vue";

import DishCardView from "@/components/knowledge/DishCard.vue";
import CommonCard from "@/components/knowledge/CommonCard.vue";

import { Card, CardType, DishCard, BusinessCard } from "@/components/knowledge";

const props = defineProps({
	card: {
		type: Object as PropType<Card>,
		required: true,
	},
});

const dish = props.card as DishCard;
const business = props.card as BusinessCard;
</script>
<template>
	<DishCardView
		v-if="props.card.type === CardType.dish"
		:card="dish"
	></DishCardView>
	<CommonCard v-else :card="business"></CommonCard>
</template>
<style scoped lang="scss"></style>
