<script setup lang="ts">
import { computed, PropType, ref } from "vue";
import { DishCard } from "@/components/knowledge";
import PulseSpinner from "@/components/UI-new/PulseSpinner.vue";

const props = defineProps({
	card: {
		type: Object as PropType<DishCard>,
		required: true,
	},
});
(props.card as any).description = `
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque nunc magna, dapibus vitae mi sed, pharetra venenatis nisi. Cras sit amet rutrum est. Morbi pellentesque posuere lacus non pretium. Sed eget molestie nunc, sed porttitor felis. Nullam tempus erat id erat volutpat condimentum. Proin tristique fringilla accumsan. Praesent varius vulputate cursus.

Pellentesque ante dolor, tempor id lacus at, volutpat sodales dui. Mauris ornare lobortis augue, nec elementum augue imperdiet et. Aliquam luctus sem ac quam posuere dignissim. Aliquam in mauris at sapien malesuada venenatis. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Proin ultricies vulputate posuere. Fusce et tincidunt ante, et molestie mauris. Pellentesque vulputate mauris at sapien ornare, ac eleifend felis bibendum. Donec at semper augue. Vestibulum malesuada elit eu dolor pulvinar, condimentum porttitor leo molestie. Donec ultricies, purus quis efficitur tincidunt, justo ligula maximus purus, ornare porta ligula orci nec diam. Ut fermentum nunc eros, eget tristique nisl molestie et. Nunc in sem sapien. Phasellus eget dignissim nunc, ut porttitor diam.;
`;

const isCompound = ref(true);

const modifiers = computed(() => {
	if (props.card.modifiers === undefined) return [];

	const temp = props.card.modifiers.map((val) => {
		return {
			sauces: val.ingredients
				.filter((ing) => ing.title.toLocaleLowerCase().includes("соус"))
				.sort((a, b) => -a.title.length + b.title.length),
			compounds: val.ingredients
				.filter((ing) => !ing.title.toLocaleLowerCase().includes("соус"))
				.sort((a, b) => -a.title.length + b.title.length),
		};
	});

	return temp.map((mod) => {
		return {
			group1: {
				sauces: mod.sauces.filter((_, i) => i % 2 === 0),
				compounds: mod.compounds.filter((_, i) => i % 2 === 0),
			},
			group2: {
				sauces: mod.sauces.filter((_, i) => i % 2 === 1),
				compounds: mod.compounds.filter((_, i) => i % 2 === 1),
			},
		};
	});
});
const modifierIndex = ref(0);
const modifier = computed(() => {
	if (!modifiers.value.length) return;
	return modifiers.value[modifierIndex.value];
});
</script>
<template>
	<div class="dish-card">
		<h2 class="title">{{ props.card.title }}</h2>
		<main class="content">
			<img :src="props.card.image" />
			<div class="info-wrapper">
				<Transition>
					<div v-if="modifier !== undefined" class="info">
						<div class="controls">
							<div class="switch">
								<button
									@click="isCompound = true"
									:class="{ active: isCompound }"
								>
									Состав
								</button>
								<button
									@click="isCompound = false"
									:class="{ active: !isCompound }"
								>
									Рецепт
								</button>
							</div>
							<div class="tools"></div>
						</div>
						<Transition name="fade" mode="out-in">
							<div v-if="isCompound" class="compound-wrapper">
								<div class="part">
									<span class="title">Соус</span>
									<div class="group">
										<ul>
											<li v-for="sauce in modifier.group1.sauces">
												<span class="li-title">{{ sauce.title }}</span>
												<span class="li-amount">{{
													Math.round(sauce.amount)
												}}</span>
											</li>
										</ul>
										<ul>
											<li v-for="sauce in modifier.group2.sauces">
												<span class="li-title">{{ sauce.title }}</span>
												<span class="li-amount">{{
													Math.round(sauce.amount)
												}}</span>
											</li>
										</ul>
									</div>
								</div>
								<div class="part">
									<span class="title">Состав</span>
									<div class="group">
										<ul>
											<li v-for="compound in modifier.group1.compounds">
												<span class="li-title">{{ compound.title }}</span>
												<span class="li-amount">{{
													Math.round(compound.amount)
												}}</span>
											</li>
										</ul>
										<ul>
											<li v-for="compound in modifier.group2.compounds">
												<span class="li-title">{{ compound.title }}</span>
												<span class="li-amount">{{
													Math.round(compound.amount)
												}}</span>
											</li>
										</ul>
									</div>
								</div>
							</div>
							<div v-else class="recept-wrapper">
								<span class="recept">{{
									(props.card as any).description
								}}</span>
							</div>
						</Transition>
					</div>
					<div v-else class="spinner-wrapper">
						<PulseSpinner class="spinner"></PulseSpinner>
					</div>
				</Transition>
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

		.info-wrapper {
			display: flex;
			flex-grow: 1;

			max-height: 100%;
			height: 480px;

			padding: 16px;
			background-color: $bg-light-blue;

			.info {
				display: flex;
				flex-direction: column;

				gap: 16px;

				width: 100%;
				max-height: 100%;
				height: 100%;

				overflow-y: auto;

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
					}
				}

				.compound-wrapper {
					display: flex;
					flex-direction: column;

					height: 100%;
					overflow-y: auto;

					gap: 16px;

					ul {
						display: flex;
						flex-direction: column;

						gap: 6px;

						list-style: none;
						margin: 0;
						padding: 0;
					}

					li {
						display: flex;
						flex-direction: row;

						align-items: center;

						gap: 24px;
						width: fit-content;

						padding: 6px 12px;
						border-radius: 8px;

						background-color: $main-white;
					}

					.title {
						font-family: Wix Madefor Display;
						font-weight: 700;
						font-size: 16px;
					}

					.part {
						display: flex;
						flex-direction: column;

						gap: 16px;

						.group {
							display: flex;
							flex-direction: row;

							gap: 24px;
						}

						.li-title {
							width: 256px;
						}
						.li-amount {
							text-align: right;
							width: 48px;
						}
					}
				}

				.recept-wrapper {
					width: 100%;
					height: fit-content;

					border-radius: 16px;
					padding: 24px;
					background-color: $main-white;

					.recept {
						font-family: Wix Madefor Display;
						font-weight: 400;
						font-size: 14px;
					}
				}
			}

			.spinner-wrapper {
				display: flex;
				justify-content: center;
				align-items: center;

				width: 100%;
				height: 100%;

				.spinner {
					width: 84px;
					height: 84px;

					color: $main-accent-blue;
				}
			}
		}
	}
}
</style>
