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

watch([currentPage, props], () => {
	const result: Array<number> = [];

	let start = 0;
	let end = -1;

	if (currentPage.value === 1) {
		start = 2;
		end = Math.min(start + middlePagesCount.value - 1, props.pageCount - 1);
	} else if (currentPage.value === props.pageCount) {
		end = props.pageCount - 1;
		start = Math.max(end - middlePagesCount.value + 1, 2);
	} else if (
		middlePages.value[0] === currentPage.value &&
		currentPage.value > 2
	) {
		start = middlePages.value[0] - 1;
		end = Math.min(start + middlePagesCount.value - 1, props.pageCount - 1);
	} else if (
		middlePages.value[middlePages.value.length - 1] === currentPage.value &&
		currentPage.value < props.pageCount - 1
	) {
		end = middlePages.value[middlePages.value.length - 1] + 1;
		start = Math.max(end - middlePagesCount.value + 1, 2);
	} else {
		start = middlePages.value[0];
		end = middlePages.value[middlePages.value.length - 1];
	}

	for (let index = start; index <= end; index++) {
		result.push(index);
	}

	middlePages.value = result;
});
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
			<input placeholder="стр." />
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
		}
	}
}
</style>
