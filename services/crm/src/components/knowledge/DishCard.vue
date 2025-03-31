<script setup lang="ts">
import { PropType } from "vue";
import { DishCard } from "@/components/knowledge";

const props = defineProps({
	card: {
		type: Object as PropType<DishCard>,
		required: true,
	},
});
</script>
<template>
	<div class="dish-card">
		<h2 class="title">{{ props.card.name }}</h2>
		<main class="content">
			<img :src="props.card.image" />
			<div class="recept"></div>
		</main>
		<footer></footer>
	</div>
</template>
<style scoped lang="scss">
.dish-card {
	display: flex;
	flex-direction: column;

	gap: 32px;
	width: 100%;
	height: fit-content;

	.title {
		font-family: Wix Madefor Display;
		font-weight: 500;
		font-size: 48px;
	}

	.content {
		display: flex;
		flex-direction: row;

		gap: 16px;

		padding: 16px;
		background-color: $main-white;

		img {
			width: 480px;
			height: 480px;
		}

		.recept {
			display: flex;
			flex-grow: 1;

			background-color: $bg-light-blue;
		}
	}
}
</style>
