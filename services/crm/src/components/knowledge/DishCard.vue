<script setup lang="ts">
import { computed, PropType, ref } from "vue";
import PulseSpinner from "@/components/UI-new/PulseSpinner.vue";
import CardMaterials from "./CardMaterials.vue";
import { DishCard } from "@/components/knowledge/types";

const props = defineProps({
	card: {
		type: Object as PropType<DishCard>,
		required: true,
	},
});
const isCompound = ref(true);

const modifiers = computed(() => {
	if (props.card.modifiers === undefined) return undefined;

	const temp = props.card.modifiers.map((val) => {
		return {
			id: val.id,
			title: val.title,
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
			id: mod.id,
			title: mod.title,
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
	if (modifiers.value === undefined) return;
	if (modifiers.value.length === 0) {
		isCompound.value = false;
		return;
	}
	return modifiers.value[modifierIndex.value];
});
const saucesExist = computed(() => {
	if (modifier.value === undefined) return false;
	return (
		modifier.value.group1.sauces.length + modifier.value.group2.sauces.length
	);
});
const compoundsExist = computed(() => {
	if (modifier.value === undefined) return false;
	return (
		modifier.value.group1.compounds.length +
		modifier.value.group2.compounds.length
	);
});

const video = computed(() => {
	if (props.card.materials === undefined) return;
	return props.card.materials.video;
});

const convertAmount = (amount: number): string => {
	return amount >= 1 ? `${amount} шт` : `${Math.round(amount * 1000)} г`;
};
</script>
<template>
	<div class="card-wrapper">
		<h2 class="title">{{ props.card.title }}</h2>
		<main class="content">
			<img :src="props.card.image" />
			<div class="info-wrapper">
				<Transition name="fade" mode="out-in">
					<div v-if="modifiers !== undefined" class="info">
						<div class="controls">
							<div class="switch">
								<button
									@click="isCompound = true"
									v-if="modifier"
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
							<div v-if="isCompound && modifier" class="compound-wrapper">
								<div class="filters" v-if="modifiers.length > 1">
									<span class="title">Фильтры</span>
									<ul>
										<li v-for="(modifier, i) in modifiers">
											<button
												@click="modifierIndex = i"
												:class="{ active: i === modifierIndex }"
											>
												{{ modifier.title }}
											</button>
										</li>
									</ul>
								</div>
								<Transition name="fade" mode="out-in">
									<div :key="modifier.id" class="compound-inner">
										<div class="part" v-if="saucesExist">
											<span class="title">Соус</span>
											<div class="group">
												<ul>
													<li v-for="sauce in modifier.group1.sauces">
														<span class="li-title">{{ sauce.title }}</span>
														<span class="li-amount">{{
															convertAmount(sauce.amount)
														}}</span>
													</li>
												</ul>
												<ul>
													<li v-for="sauce in modifier.group2.sauces">
														<span class="li-title">{{ sauce.title }}</span>
														<span class="li-amount">{{
															convertAmount(sauce.amount)
														}}</span>
													</li>
												</ul>
											</div>
										</div>
										<div class="part" v-if="compoundsExist">
											<span class="title">Состав</span>
											<div class="group">
												<ul>
													<li v-for="compound in modifier.group1.compounds">
														<span class="li-title">{{ compound.title }}</span>
														<span class="li-amount">{{
															convertAmount(compound.amount)
														}}</span>
													</li>
												</ul>
												<ul>
													<li v-for="compound in modifier.group2.compounds">
														<span class="li-title">{{ compound.title }}</span>
														<span class="li-amount">{{
															convertAmount(compound.amount)
														}}</span>
													</li>
												</ul>
											</div>
										</div>
									</div>
								</Transition>
							</div>
							<div v-else class="recept-wrapper">
								<span
									class="recept"
									v-for="line in props.card.description.split('\n')"
									>{{ line }}<br
								/></span>
							</div>
						</Transition>
					</div>
					<div v-else class="spinner-wrapper">
						<PulseSpinner class="spinner"></PulseSpinner>
					</div>
				</Transition>
			</div>
		</main>
		<Transition name="fade" mode="out-in">
			<footer v-if="props.card.materials" class="materials">
				<video v-if="video" class="video" controls>
					<source :src="video.url" type="video/mp4" />
					{{ video.name }}
				</video>
				<CardMaterials
					v-if="props.card.materials.materials.length"
					:materials="props.card.materials.materials"
				></CardMaterials>
			</footer>
			<div v-else class="spinner-wrapper">
				<PulseSpinner class="spinner"></PulseSpinner>
			</div>
		</Transition>
	</div>
</template>
<style scoped lang="scss">
@import "bootstrap/scss/functions";
@import "bootstrap/scss/variables";
@import "bootstrap/scss/mixins";

@import url("./style.scss");

.card-wrapper {
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
			position: relative;
			display: flex;
			flex-grow: 1;

			overflow-x: auto;
			max-height: 100%;
			height: 480px;
			width: 100%;

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

				.title {
					font-family: Wix Madefor Display;
					font-weight: 700;
					font-size: 16px;
				}

				.filters {
					display: flex;
					flex-direction: column;

					max-width: 100%;
					gap: 16px;

					ul {
						display: flex;
						flex-direction: row;
						width: fit-content;
						max-width: 100%;
						flex-wrap: wrap;

						gap: 8px;

						border-radius: 16px;
						background-color: $main-white;

						button {
							min-width: 84px;
							height: 42px;
							padding: 8px 14px;

							background-color: $main-white;
							border: none;
							color: $main-accent-blue;
							border-radius: 24px;
							transition: background-color 0.25s;

							&.active,
							&:hover {
								color: $main-white;
								background-color: $sec-gray-blue;
							}
						}
					}
				}

				.compound-wrapper {
					display: flex;
					flex-direction: column;

					gap: 16px;
					height: 100%;

					.compound-inner {
						display: flex;
						flex-direction: column;

						height: 100%;

						gap: 16px;

						.part {
							display: flex;
							flex-direction: column;

							gap: 16px;

							ul {
								display: flex;
								flex-direction: column;

								gap: 6px;
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
								width: 56px;
							}
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
		}

		@include media-breakpoint-down(xxl) {
			flex-direction: column;
			align-items: center;
		}

		@include media-breakpoint-down(xl) {
			.info-wrapper {
				.info {
					.compound-wrapper {
						.compound-inner {
							.part {
								.group {
									flex-direction: column;
								}
							}
						}
					}
				}
			}
		}
	}

	.materials {
		.video {
			width: 100%;
			height: 480px;
		}
	}
}
</style>
