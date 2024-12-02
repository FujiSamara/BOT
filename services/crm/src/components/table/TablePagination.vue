<script setup lang="ts">
import { computed, ref, Ref, watch } from "vue";

const props = defineProps({
	pageCount: {
		type: Number,
		required: true,
	},
});
const currentPage = defineModel("currentPage", {
	required: true,
	default: 1,
});

const middlePagesCount = computed(() => {
	return Math.min(props.pageCount - 2, 5);
});

const middlePages: Ref<Array<number>> = ref([]);

const inputValue = ref(currentPage.value);

watch([currentPage, props], () => {
	const result: Array<number> = [];
	const middle = props.pageCount / 2;

	let start = 0;
	let end = -1;

	if (currentPage.value < middle) {
		start = Math.max(currentPage.value - 1, 1);
		end = start + middlePagesCount.value;
	} else {
		end = Math.min(currentPage.value + 1, props.pageCount);
		start = end - middlePagesCount.value;
	}

	for (let index = start; index <= end; index++) {
		if (index != 1 && index != props.pageCount) result.push(index);
	}

	middlePages.value = result;
});

const onInput = (e: Event) => {
	const intValue = parseInt((e.target as HTMLInputElement).value);

	if (isNaN(intValue)) {
		console.log("kek");
		inputValue.value = 1;
		return;
	}

	if (intValue > 0 && intValue <= props.pageCount) {
		currentPage.value = intValue;
		inputValue.value = intValue;
	}
};
</script>

<template>
	<div class="pagination">
		<p class="pag-info">Страница {{ currentPage }} из {{ props.pageCount }}</p>
		<ul class="pag-buttons">
			<li
				class="pag-button"
				@click.prevent="currentPage = 1"
				:class="{ current: 1 === currentPage }"
			>
				<span>{{ 1 }}</span>
			</li>
			<p class="ellipsis" v-if="props.pageCount > 2 && middlePages[0] > 2">—</p>
			<li
				class="pag-button"
				v-for="num in middlePages"
				@click.prevent="currentPage = num"
				:class="{
					current: num === currentPage,
				}"
			>
				<span>{{ num }}</span>
			</li>
			<span
				class="ellipsis"
				v-if="
					props.pageCount > 2 &&
					middlePages[middlePages.length - 1] < props.pageCount - 1
				"
			>
				—
			</span>
			<li
				v-if="props.pageCount > 1"
				class="pag-button"
				@click.prevent="currentPage = props.pageCount"
				:class="{
					current: props.pageCount === currentPage,
				}"
			>
				<span>{{ props.pageCount }}</span>
			</li>
		</ul>
		<div class="pag-to-page">
			<span>Перейти к странице</span>
			<input
				type="number"
				step="1"
				min="0"
				:max="props.pageCount"
				placeholder="стр."
				@change="onInput"
				:value="inputValue"
			/>
		</div>
	</div>
</template>

<style scoped lang="scss">
.pagination {
	display: flex;
	flex-direction: row;
	justify-content: space-between;
	align-items: center;

	flex-grow: 0;
	flex-shrink: 0;

	margin: 0;

	border-radius: 8px;
	padding: 24px 0;

	background: transparent;
	font-size: 14px;
	font-family: Wix Madefor Display;
	font-weight: 500;
	line-height: 17.64px;

	.pag-info {
		margin: 0;
		color: $text-color;
	}

	.pag-buttons {
		display: flex;
		flex-direction: row;
		align-items: center;

		gap: 8px;

		list-style: none;
		margin: 0;
		padding: 0;
		height: 100%;

		.pag-button {
			display: flex;
			justify-content: center;
			align-items: center;

			height: inherit;
			padding: 12px 16px;
			border-radius: 8px;

			background-color: $fuji-white;
			cursor: pointer;

			color: #474747cc;

			transition:
				background-color 0.3s,
				box-shadow 0.3s,
				color 0.3s;

			&.current {
				background-color: $fuji-blue;
				color: $text-color-white;
			}

			&:hover {
				background-color: $fuji-blue;
				box-shadow: 0px 0px 4px 0px $fuji-blue;
				color: $text-color-white;
			}
		}

		.ellipsis {
			user-select: none;
			margin: 0;
			font-family: Stolzl;
			font-size: 14px;
			color: #474747cc;
		}
	}

	.pag-to-page {
		display: flex;
		flex-direction: row;
		align-items: center;

		height: 100%;
		gap: 8px;

		color: $text-color;

		input {
			width: 64px;
			height: inherit;

			border-radius: 8px;
			padding: 12px 16px;
			border: none;
			outline: none;

			&::placeholder {
				color: #47474780;
			}

			&::-webkit-outer-spin-button,
			&::-webkit-inner-spin-button {
				-webkit-appearance: none;
				margin: 0;
			}
		}
	}
}
</style>
