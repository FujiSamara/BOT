<template>
	<div class="wrapper">
		<BorderInput
			placeholder="Фильтр"
			v-model:value="value"
			disabled
		></BorderInput>
		<ClickableIcon
			@click="listVisible = !listVisible"
			class="icon"
			img-src="/img/filter.svg"
		></ClickableIcon>
		<div class="list-wrapper">
			<Transition>
				<SelectList
					@select="onClick"
					class="list"
					v-if="listVisible"
					:select-list="list.filter((el) => el !== value)"
				></SelectList>
			</Transition>
		</div>
	</div>
</template>
<script setup lang="ts">
import { ref } from "vue";
import SelectList from "../UI/SelectList.vue";
import BorderInput from "../UI/BorderInput.vue";
import ClickableIcon from "../UI/ClickableIcon.vue";
import { FilterSchema } from "@/table";

const props = defineProps({
	group: {
		type: Number,
		required: true,
	},
});
const filters = defineModel("filters");

const listVisible = ref(false);
const value = ref("Не выбрано");
const list = ref([
	"Не выбрано",
	"Согласование ЦФО",
	"Согласование ЦЗ",
	"Согласование КРУ",
	"Согласование помощник юрисконсульта",
	"Согласование бух.",
	"Согласование кассир",
	"Выплачена",
	"Отклонена",
]);

const onClick = async (index: number) => {
	value.value = list.value.filter((el) => el !== value.value)[index];
	listVisible.value = false;

	let tempFilters: Array<FilterSchema> = [];

	switch (value.value) {
		case "Согласование ЦФО":
			tempFilters = [
				{
					column: "fac_state",
					value: "pending_approval",
				},
			];
			break;

		case "Согласование ЦЗ":
			tempFilters = [
				{
					column: "cc_state",
					value: "pending_approval",
				},
			];
			break;

		case "Согласование КРУ":
			tempFilters = [
				{
					column: "kru_state",
					value: "pending_approval",
				},
			];
			break;

		case "Согласование помощник юрисконсульта":
			tempFilters = [
				{
					column: "paralegal_state",
					value: "pending_approval",
				},
			];
			break;

		case "Согласование бух.":
			tempFilters = [
				{
					column: "accountant_cash_state",
					value: "pending_approval",
					groups: [props.group],
				},
				{
					column: "accountant_card_state",
					value: "pending_approval",
					groups: [props.group],
				},
			];
			break;

		case "Согласование кассир":
			tempFilters = [
				{
					column: "teller_cash_state",
					value: "pending_approval",
					groups: [props.group],
				},
				{
					column: "teller_card_state",
					value: "pending_approval",
					groups: [props.group],
				},
			];
			break;

		case "Выплачена":
			tempFilters = [
				{
					column: "teller_cash_state",
					value: "approved",
					groups: [props.group],
				},
				{
					column: "teller_card_state",
					value: "approved",
					groups: [props.group],
				},
			];
			break;
		case "Отклонена":
			tempFilters = [
				{
					column: "fac_state",
					value: "denied",
					groups: [props.group],
				},
				{
					column: "cc_state",
					value: "denied",
					groups: [props.group],
				},
				{
					column: "kru_state",
					value: "denied",
					groups: [props.group],
				},
				{
					column: "paralegal_state",
					value: "denied",
					groups: [props.group],
				},
				{
					column: "accountant_cash_state",
					value: "denied",
					groups: [props.group],
				},
				{
					column: "accountant_card_state",
					value: "denied",
					groups: [props.group],
				},
				{
					column: "teller_cash_state",
					value: "denied",
					groups: [props.group],
				},
				{
					column: "teller_card_state",
					value: "denied",
					groups: [props.group],
				},
			];
			break;
	}

	filters.value = tempFilters;
};
</script>
<style scoped>
.wrapper {
	display: flex;
	gap: 10px;
}
.icon {
	width: 20px;
}
.list-wrapper {
	position: absolute;
	top: 100%;
	min-width: 200px;
	z-index: 2;
	background-color: #ffffff;
}

.v-enter-active,
.v-leave-active {
	transition: all 0.5s ease;
}

.v-enter-from,
.v-leave-to {
	max-height: 0;
}
</style>
