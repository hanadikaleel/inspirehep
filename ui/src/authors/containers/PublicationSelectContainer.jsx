import { connect } from 'react-redux';
import { Checkbox } from 'antd';

import { setPublicationSelection } from '../../actions/authors';

const stateToProps = (state, { recordId }) => ({
  checked: state.authors.get('publicationSelection').has(recordId),
});

const dispatchToProps = (dispatch, { recordId }) => ({
  onChange(event) {
    dispatch(setPublicationSelection([recordId], event.target.checked));
  },
});

export default connect(stateToProps, dispatchToProps)(Checkbox);
