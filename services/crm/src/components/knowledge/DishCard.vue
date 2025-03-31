<script setup lang="ts">
import { PropType, ref } from "vue";
import { DishCard } from "@/components/knowledge";

const props = defineProps({
	card: {
		type: Object as PropType<DishCard>,
		required: true,
	},
});

const isCompound = ref(true);
</script>
<template>
	<div class="dish-card">
		<h2 class="title">{{ props.card.name }}</h2>
		<main class="content">
			<img :src="props.card.image" />
			<div class="info">
				<div class="controls">
					<div class="switch">
						<button :class="{ active: isCompound }">Состав</button>
						<button :class="{ active: !isCompound }">Рецепт</button>
					</div>
					<div class="tools"></div>
				</div>
			</div>
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

		.info {
			display: flex;
			flex-grow: 1;

			padding: 16px;
			background-color: $bg-light-blue;

			.controls {
				display: flex;
				flex-direction: row;

				justify-content: space-between;
				align-items: center;
				width: 100%;

				height: 40px;

				.switch {
					display: flex;
					flex-direction: row;

					gap: 8px;

					button {
						width: 112px;
						height: 39px;

						border: 1px solid $sec-dark-gray-25;
						background-color: $bg-light-blue;
						border-radius: 4px;

						&.active,
						&:hover {
							border-color: $main-accent-blue;
							background-color: $main-white;
						}

						transition:
							border-color 0.25s,
							background-color 0.25s;
					}
				}

				.tools {
					height: 28px;
					width: 68px;
					background-color: black;
				}
			}
		}
	}
}
</style>
