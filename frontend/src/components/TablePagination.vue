<template>
	<ul class="pagination-wrapper">
		<li
			class="page-button"
			@click.prevent="currentPage = 1"
			:class="{ currentPage: 1 === currentPage }"
		>
			{{ 1 }}
		</li>
		<p class="ellipsis" v-if="props.pageCount > 2 && middlePages[0] > 2">...</p>
		<li
			class="page-button"
			v-for="num in middlePages"
			@click.prevent="currentPage = num"
			:class="{
				currentPage: num === currentPage,
			}"
		>
			{{ num }}
		</li>
		<p
			class="ellipsis"
			v-if="
				props.pageCount > 2 &&
				middlePages[middlePages.length - 1] < props.pageCount - 1
			"
		>
			...
		</p>
		<li
			v-if="props.pageCount > 1"
			class="page-button"
			@click.prevent="currentPage = props.pageCount"
			:class="{
				currentPage: props.pageCount === currentPage,
			}"
		>
			{{ props.pageCount }}
		</li>
	</ul>
</template>
<script setup lang="ts">
import { computed, Ref, ref, watch } from "vue";

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
	return Math.min(props.pageCount - 2, 6);
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
<style scoped>
.pagination-wrapper {
	list-style: none;
	background-color: #ffffff;
	border: 1px solid #e6e6e6;
	border-top-left-radius: 15px;
	border-top-right-radius: 15px;

	margin: 0;
	padding: 0;
	display: flex;
	flex-direction: row;
	gap: 4px;
	height: 60px;
	max-height: 20%;
	width: 300px;
	max-width: 100%;
	overflow: hidden;
	justify-content: center;
	align-items: center;
	flex-shrink: 0;
}

.page-button {
	width: 24px;
	height: 24px;
	display: flex;
	justify-content: center;
	align-items: center;

	user-select: none;
	cursor: pointer;
	border: 1px solid #993ca6;
	font-family: Stolzl;
	color: #993ca6;
	font-size: 20px;
	border-radius: 5px;
	transition: 0.3s;
}

.page-button:hover {
	transform: scale(1.05);
	transition: 0.3s;
	background-color: #e6e6e6;
}

.currentPage {
	background-color: #ffeaff !important;
}

.ellipsis {
	user-select: none;
	margin: 0;
	font-family: Stolzl;
	font-size: 20px;
	color: #993ca6;
}
</style>
